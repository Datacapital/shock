from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración de la aplicación"""
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)
    
    # Supabase (OBLIGATORIO)
    supabase_url: str
    supabase_key: str
    
    # Configuración general
    timezone: str = "America/Caracas"
    port: int = 8000
    host: str = "0.0.0.0"
    
    # Horarios de actualización
    hora_actualizacion_bvc: str = "17:00"


settings = Settings()
