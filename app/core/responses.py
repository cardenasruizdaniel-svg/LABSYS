from typing import Any


class ApiResponse:

    @staticmethod
    def success(
        data: Any = None,
        message: str = "Proceso realizado correctamente"
    ):

        return {

            "success": True,

            "message": message,

            "data": data

        }

    @staticmethod
    def error(
        message: str,
        data: Any = None
    ):

        return {

            "success": False,

            "message": message,

            "data": data

        }