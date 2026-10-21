import bcrypt from "bcryptjs";
import User from "../models/User.js";
import { generateToken } from "../utils/generateToken.js";

export async function register(req, res, next) {
  try {
    const { name, email, password } = req.body;
    const normalizedEmail = String(email || "").trim().toLowerCase();
    if (!name?.trim() || !normalizedEmail || !password) return res.status(400).json({ message: "name, email and password are required" });
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(normalizedEmail)) return res.status(400).json({ message: "A valid email is required" });
    if (password.length < 8) return res.status(400).json({ message: "Password must be at least 8 characters" });
    const existing = await User.findOne({ email: normalizedEmail });
    if (existing) return res.status(409).json({ message: "A user with this email already exists" });
    const passwordHash = await bcrypt.hash(password, 12);
    const user = await User.create({ name: name.trim(), email: normalizedEmail, passwordHash, role: "doctor" });
    res.status(201).json({ _id: user._id, name: user.name, email: user.email, role: user.role, token: generateToken(user._id, user.role) });
  } catch (err) { next(err); }
}

export async function login(req, res, next) {
  try {
    const { email, password } = req.body;
    const normalizedEmail = String(email || "").trim().toLowerCase();
    if (!normalizedEmail || !password) return res.status(400).json({ message: "email and password are required" });
    const user = await User.findOne({ email: normalizedEmail });
    if (!user || user.status !== "active" || !(await bcrypt.compare(password, user.passwordHash))) return res.status(401).json({ message: "Invalid credentials" });
    res.json({ _id: user._id, name: user.name, email: user.email, role: user.role, token: generateToken(user._id, user.role) });
  } catch (err) { next(err); }
}

export async function me(req, res) { res.json(req.user); }

export async function createUserByAdmin(req, res, next) {
  try {
    const { name, email, password, role = "doctor" } = req.body;
    const normalizedEmail = String(email || "").trim().toLowerCase();
    if (!name?.trim() || !normalizedEmail || !password) return res.status(400).json({ message: "name, email and password are required" });
    if (!["admin", "doctor", "staff"].includes(role)) return res.status(400).json({ message: "Invalid role" });
    if (password.length < 8) return res.status(400).json({ message: "Password must be at least 8 characters" });
    if (await User.findOne({ email: normalizedEmail })) return res.status(409).json({ message: "A user with this email already exists" });
    const passwordHash = await bcrypt.hash(password, 12);
    const user = await User.create({ name: name.trim(), email: normalizedEmail, passwordHash, role, status: "active" });
    res.status(201).json({ _id: user._id, name: user.name, email: user.email, role: user.role, status: user.status });
  } catch (err) { next(err); }
}
