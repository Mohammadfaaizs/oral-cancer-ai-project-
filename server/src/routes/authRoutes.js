import express from "express";
import { register, login, me, createUserByAdmin } from "../controllers/authController.js";
import { protect, requireRole } from "../middleware/authMiddleware.js";
import User from "../models/User.js";

const router = express.Router();
router.post("/register", register);
router.post("/login", login);
router.get("/me", protect, me);
router.post("/users", protect, requireRole("admin"), createUserByAdmin);
router.get("/users", protect, requireRole("admin"), async (req, res, next) => { try { res.json(await User.find().select("-passwordHash").sort({ createdAt: -1 })); } catch (e) { next(e); } });
router.patch("/users/:id/status", protect, requireRole("admin"), async (req, res, next) => { try { if (String(req.user._id) === req.params.id) return res.status(400).json({ message: "You cannot disable your own account" }); const user = await User.findByIdAndUpdate(req.params.id, { status: req.body.status }, { new: true }).select("-passwordHash"); if (!user) return res.status(404).json({ message: "User not found" }); res.json(user); } catch (e) { next(e); } });

export default router;
