from fastapi import APIRouter

router = APIRouter(
    prefix="/health",
    tags=["Health"]
)


@router.get("")
def health():

    return {

        "success": True,

        "application": "LABSYS DIALIZAR",

        "status": "ONLINE",

        "version": "1.0.0"

    }