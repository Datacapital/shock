from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuración de la aplicación"""
    
    # Supabase (OBLIGATORIO)
    supabase_url: str
    supabase_key: str
    
    # Configuración general
    timezone: str = "America/Caracas"
    port: int = 8000
    host: str = "0.0.0.0"
    
    # Horarios de actualización
    hora_actualizacion_bvc: str = "17:00"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        fields = {
            "supabase_url": {"env": "SUPABASE_URL"},
            "supabase_key": {"env": "SUPABASE_KEY"},
        }


settings = Settings()
