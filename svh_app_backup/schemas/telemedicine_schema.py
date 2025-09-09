from models.telemedicine_model import AppointmentModel
from parsers.telemedicine_parser import AppointmentCreate, AppointmentResponse
from datetime import datetime

class TelemedicineParser:
    @staticmethod
    def parse_create(appointment: AppointmentCreate) -> AppointmentModel:
        return AppointmentModel(
            user_id=appointment.user_id,
            doctor_id=appointment.doctor_id,
            datetime=appointment.datetime,
            mode=appointment.mode,
            status=appointment.status,
            notes=appointment.notes,
            created_at=datetime.utcnow()
        )

    @staticmethod
    def to_json(appointment: AppointmentModel) -> AppointmentResponse:
        return AppointmentResponse.from_orm(appointment)
