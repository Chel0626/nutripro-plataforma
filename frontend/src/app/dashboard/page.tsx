"use client";
import React, { useEffect, useState } from "react";
import { onAuthStateChanged, signOut, User } from "firebase/auth";
import { collection, getDocs } from "firebase/firestore";
import { auth, db } from "@/lib/firebase";
import { useRouter } from "next/navigation";

export default function Dashboard() {
  const [user, setUser] = useState<User | null>(null);
  const [pacientes, setPacientes] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (firebaseUser) => {
      if (!firebaseUser) {
        router.push("/login");
      } else {
        setUser(firebaseUser);
        // Buscar pacientes do Firestore
        const snapshot = await getDocs(collection(db, "pacientes"));
        setPacientes(snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() })));
        setLoading(false);
      }
    });
    return () => unsubscribe();
  }, [router]);

  const handleLogout = async () => {
    await signOut(auth);
    router.push("/login");
  };

  if (loading) {
    return <div className="flex min-h-screen items-center justify-center">Carregando...</div>;
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-green-100 to-blue-100 p-4 flex flex-col items-center">
      <div className="w-full max-w-2xl bg-white rounded-xl shadow-lg p-6 mt-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-2xl font-bold text-green-700">Dashboard</h2>
          <button onClick={handleLogout} className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded">Sair</button>
        </div>
        <h3 className="text-lg font-semibold mb-2">Pacientes</h3>
        {pacientes.length === 0 ? (
          <div className="text-gray-500">Nenhum paciente cadastrado.</div>
        ) : (
          <ul className="divide-y">
            {pacientes.map((p) => (
              <li key={p.id} className="py-2 flex flex-col sm:flex-row sm:justify-between">
                <span className="font-medium">{p.nome_completo || p.nome || "(Sem nome)"}</span>
                <span className="text-gray-500 text-sm">{p.email || ""}</span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </main>
  );
}
