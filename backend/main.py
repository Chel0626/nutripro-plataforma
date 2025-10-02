from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from google.cloud import firestore
import firebase_admin
from firebase_admin import credentials, auth
import os

# Inicialização do Firebase Admin SDK
FIREBASE_CRED_PATH = os.getenv('FIREBASE_CRED_PATH', '../firebase/serviceAccountKey.json')
if not firebase_admin._apps:
    cred = credentials.Certificate(FIREBASE_CRED_PATH)
    firebase_admin.initialize_app(cred)

db = firestore.Client()

app = FastAPI(title="NutriPro API", version="1.0")

# CORS para permitir acesso do frontend/mobile
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "NutriPro API rodando!"}

@app.get("/pacientes")
def listar_pacientes():
    pacientes_ref = db.collection('pacientes')
    docs = pacientes_ref.stream()
    pacientes = [{"id": doc.id, **doc.to_dict()} for doc in docs]
    return {"pacientes": pacientes}

# Exemplo de endpoint protegido por autenticação Firebase
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
security = HTTPBearer()

def verify_firebase_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        decoded_token = auth.verify_id_token(credentials.credentials)
        return decoded_token
    except Exception:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado.")

@app.get("/user/profile")
def user_profile(user=Depends(verify_firebase_token)):
    return {"user": user}
