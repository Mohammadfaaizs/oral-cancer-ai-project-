import { createContext, useContext, useEffect, useState } from "react";
import api from "../services/api";
const AuthContext=createContext(null);
export function AuthProvider({children}){
 const [user,setUser]=useState(null),[loading,setLoading]=useState(true);
 useEffect(()=>{const token=localStorage.getItem("token"); if(!token){setLoading(false);return;} api.get("/auth/me").then(r=>setUser(r.data)).catch(()=>localStorage.removeItem("token")).finally(()=>setLoading(false));},[]);
 async function login(email,password){const r=await api.post("/auth/login",{email,password}); localStorage.setItem("token",r.data.token); setUser(r.data); return r.data;}
 async function register(name,email,password){const r=await api.post("/auth/register",{name,email,password}); localStorage.setItem("token",r.data.token); setUser(r.data); return r.data;}
 function logout(){localStorage.removeItem("token");setUser(null);}
 return <AuthContext.Provider value={{user,loading,login,register,logout}}>{children}</AuthContext.Provider>
}
export const useAuth=()=>useContext(AuthContext);
