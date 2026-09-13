"""HL7 v2.5 — parseur et constructeur pur Python (ADR-0005/0007).

Messages supportés (les 4 flux vitaux d'un SIH) :
- ADT^A08 : mise à jour démographique patient
- ORM^O01 : commande d'examen (labo/imagerie)
- ORU^R01 : résultat d'observation non sollicité
- SIU^S12 : notification de rendez-vous
- ACK     : acquittement générique
Framing MLLP (0x0B ... 0x1C 0x0D) pour l'intégration Mirth/analyteurs.
"""
from __future__ import annotations

from datetime import datetime

VT, FS, RS, GS, CR, EB = "\x0b", "|", "~", "^", "\r", "&"
FILL = '""'


def _now_hl7() -> str:
    return datetime.now().strftime("%Y%m%d%H%M%S")


class HL7Message:
    """Représentation d'un message HL7 v2 : segments → champs → répétitions → composants.

    Hiérarchie : segment|champ^composant&~répétition.
    Convention MSH : seg[1] = MSH-2 (encodages), seg[8] = MSH-9 (type).
    """

    def __init__(self, raw: str) -> None:
        self.raw = raw
        self.segments: list[list[str]] = []
        for line in raw.strip(CR).split(CR):
            if line:
                self.segments.append(line.split(FS))

    @property
    def message_type(self) -> str:
        m9 = self.field("MSH", 8)
        m9_trigger = self.field("MSH", 8, component=1)
        return m9 if not m9_trigger else f"{m9}^{m9_trigger}"

    def segment(self, name: str) -> list[str] | None:
        for seg in self.segments:
            if seg and seg[0] == name:
                return seg
        return None

    def field(self, segment: str, index: int, repeat: int = 0,
              component: int = 0) -> str:
        """Renvoie la valeur d'un champ (ex. field('PID', 3) = PID-3).

        index suit la convention segments[] : PID-3 est à l'index 3
        (le nom du segment occupe l'index 0) ; pour MSH, MSH-9 est à l'index 8
        (MSH-1 étant le séparateur lui-même).
        """
        seg = self.segment(segment)
        if not seg or len(seg) <= index:
            return ""
        repeats = seg[index].split(RS)
        if len(repeats) <= repeat:
            return ""
        comps = repeats[repeat].split(GS)
        return comps[component] if len(comps) > component else ""


def parse(raw: str) -> HL7Message:
    """Parse un message HL7 (avec ou sans framing MLLP)."""
    return HL7Message(raw.replace(VT, "").replace("\x1c\r", ""))


def _msh(sending: str, receiving: str, msg_type: str, control_id: str,
         trigger: str = "") -> str:
    """Segment MSH-1..MSH-12 conforme v2.5 (encodages ^~\\&)."""
    mtype = msg_type if "^" in msg_type else f"{msg_type}^{trigger}"
    return FS.join(["MSH", "^~\\&", sending, sending, receiving, receiving,
                    _now_hl7(), "", mtype, control_id, "P", "2.5"])


def build_adt_a08(patient: dict, control_id: str = "MSG00001") -> str:
    """Mise à jour démographique — PID : id, nom^prénom, dob, sexe, tel."""
    pid = (f"PID|1||{patient.get('numero_dossier', '')}||"
           f"{patient.get('nom', '')}^{patient.get('prenoms', '')}||"
           f"{patient.get('date_naissance', '')}|{patient.get('sexe', '')}|||"
           f"{patient.get('adresse', '')}||{patient.get('telephone', '')}")
    return CR.join([_msh("PATIENT-SERVICE", "INTEGRATION", "ADT", control_id, "A08"), pid])


def build_orm_o01(order: dict, control_id: str = "MSG00002") -> str:
    """Commande d'examen — OBR : n° commande, code examen, prescripteur, priorité."""
    obr = (f"OBR|1|{order.get('id', '')}|{order.get('accession', '')}|"
           f"{order.get('code_examen', '')}^{order.get('libelle_examen', '')}|"
           f"|{_now_hl7()}|||{order.get('urgent', 'R')}|||{order.get('prescripteur', '')}")
    return CR.join([_msh("SERVICE-CLINIQUE", "LABORATORY", "ORM", control_id, "O01"), obr])


def build_oru_r01(result: dict, patient: dict,
                  control_id: str = "MSG00003") -> str:
    """Résultat non sollicité — OBX : code LOINC, valeur, unité, flag normal/anormal."""
    flag = "N" if result.get("dans_reference", True) else "A"
    obx = (f"OBX|1|NM|{result.get('loinc', '')}^{result.get('analyse', '')}|"
           f"|{result.get('valeur', '')}|{result.get('unite', '')}|"
           f"{result.get('ref_basse', '')}-{result.get('ref_haute', '')}|{flag}|||F")
    pid = (f"PID|1||{patient.get('numero_dossier', '')}||"
           f"{patient.get('nom', '')}^{patient.get('prenoms', '')}")
    return CR.join([_msh("LABORATORY", "INTEGRATION", "ORU", control_id, "R01"),
                    pid, obx])


def build_siu_s12(appointment: dict, patient: dict,
                  control_id: str = "MSG00004") -> str:
    """Rendez-vous — AIS : code acte planifié."""
    sch = (f"SCH|1|{appointment.get('id', '')}|||{_now_hl7()}|"
           f"{appointment.get('duree_min', 30)}|min")
    ais = f"AIS|1||{appointment.get('code_acte', '')}^{appointment.get('libelle_acte', '')}"
    pid = (f"PID|1||{patient.get('numero_dossier', '')}||"
           f"{patient.get('nom', '')}^{patient.get('prenoms', '')}")
    return CR.join([_msh("APPOINTMENT", "INTEGRATION", "SIU", control_id, "S12"),
                    sch, pid, ais])


def ack_for(message: HL7Message, ok: bool = True) -> str:
    """Génère l'ACK (MSA) pour un message reçu — code AA (accept) ou AE (erreur)."""
    msh = message.segment("MSH")
    control_id = msh[9] if msh and len(msh) > 9 else "UNKNOWN"
    msa = f"MSA|{'AA' if ok else 'AE'}|{control_id}"
    sending = msh[2] if msh and len(msh) > 2 else "APP"
    receiving = msh[4] if msh and len(msh) > 4 else "MEDISUITE"
    return CR.join([_msh(receiving, sending, "ACK", f"ACK{control_id}"), msa])

# ---------------------------------------------------------------- MLLP


def mllp_frame(message: str) -> bytes:
    """Encadre un message pour la transmission MLLP : <VT>message<FS><CR>."""
    return (VT + message + "\x1c\r").encode("ascii", errors="replace")


def mllp_unframe(payload: bytes) -> str:
    """Extrait le message d'un flux MLLP (peut contenir plusieurs frames)."""
    return payload.decode("ascii", errors="replace").replace(VT, "").replace("\x1c\r", "")
