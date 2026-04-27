from fastapi import APIRouter, Depends, HTTPException, status
from app.models.user import LoginRequest, AuthResponse, UserResponse
from app.models.pfe import MessageResponse
from app.services.supabase_service import get_supabase_service, SupabaseService
from app.deps import get_current_user, get_optional_user
from uuid import UUID


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=AuthResponse)
async def login(
    credentials: LoginRequest,
    supabase_service: SupabaseService = Depends(get_supabase_service)
):
    try:
        client = supabase_service.supabase.auth.sign_in_with_password({
            "email": credentials.email,
            "password": credentials.password
        })
        
        if not client.session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        try:
            profile = await supabase_service.get_user_profile(str(client.user.id))
            if not profile:
                await supabase_service.create_user_profile(str(client.user.id))
        except Exception as e:
            print(f"Profile error (ignorable): {e}")
        
        return AuthResponse(
            session={"access_token": client.session.access_token, "expires_in": client.session.expires_in},
            user=UserResponse(
                id=str(client.user.id),
                email=client.user.email,
                email_confirmed_at=client.user.email_confirmed_at
            )
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}"
        )


@router.post("/register", response_model=AuthResponse)
async def register(
    credentials: LoginRequest,
    supabase_service: SupabaseService = Depends(get_supabase_service)
):
    try:
        client = supabase_service.supabase.auth.sign_up({
            "email": credentials.email,
            "password": credentials.password
        })
        
        if not client.session:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Registration failed"
            )
        
        if client.user:
            try:
                await supabase_service.create_user_profile(str(client.user.id))
            except Exception as e:
                print(f"Profile creation error (ignorable): {e}")
        
        return AuthResponse(
            session={"access_token": client.session.access_token, "expires_in": client.session.expires_in},
            user=UserResponse(
                id=str(client.user.id),
                email=client.user.email,
                email_confirmed_at=client.user.email_confirmed_at
            )
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Registration failed: {str(e)}"
        )


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: dict = Depends(get_current_user)
):
    return UserResponse(
        id=current_user["id"],
        email=current_user.get("email", ""),
        email_confirmed_at=current_user.get("email_confirmed_at")
    )


@router.post("/logout", response_model=MessageResponse)
async def logout(
    supabase_service: SupabaseService = Depends(get_supabase_service)
):
    try:
        supabase_service.supabase.auth.sign_out()
        return MessageResponse(message="Logged out successfully")
    except Exception:
        return MessageResponse(message="Logged out successfully")