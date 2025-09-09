from models.doctor_model import DoctorModel
from parsers.doctor_parser import DoctorCreate, DoctorResponse

class DoctorParser:
    @staticmethod
    def parse_create(doctor: DoctorCreate) -> DoctorModel:
        return DoctorModel(
            name=doctor.name,
            specialization=doctor.specialization,
            qualifications=doctor.qualifications,
            languages=doctor.languages,
            clinic_address=doctor.clinic_address
        )

    @staticmethod
    def to_json(doctor: DoctorModel) -> DoctorResponse:
        return DoctorResponse.from_orm(doctor)
