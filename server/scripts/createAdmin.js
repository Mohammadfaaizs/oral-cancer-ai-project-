import dotenv from 'dotenv';
import bcrypt from 'bcryptjs';
import mongoose from 'mongoose';
import User from '../src/models/User.js';

dotenv.config();
const args=process.argv.slice(2); const get=k=>{const i=args.indexOf(`--${k}`);return i>=0?args[i+1]:undefined};
const name=get('name')||process.env.ADMIN_NAME; const email=(get('email')||process.env.ADMIN_EMAIL||'').toLowerCase(); const password=get('password')||process.env.ADMIN_PASSWORD;
if(!name||!email||!password) { console.error('Usage: npm run create-admin -- --name "System Admin" --email admin@example.com --password "StrongPassword"'); process.exit(1); }
if(password.length<12) { console.error('Admin password must be at least 12 characters.'); process.exit(1); }
await mongoose.connect(process.env.MONGO_URI||'mongodb://127.0.0.1:27017/oral_cancer_ai');
const hash=await bcrypt.hash(password,12); const user=await User.findOneAndUpdate({email},{name,email,passwordHash:hash,role:'admin',status:'active'},{upsert:true,new:true,setDefaultsOnInsert:true});
console.log(`Admin ready: ${user.email}`); await mongoose.disconnect();
