// ================= IMPORTS =================
const express = require("express");
const path = require("path");
const nodemailer = require("nodemailer");

// ================= APP =================
const app = express();
const PORT = 5000;

// ================= MIDDLEWARE =================
app.use(express.json());

// ================= STATIC FILES =================
// ✅ ONLY frontend folder serve karo
app.use(express.static(path.join(__dirname, "../frontend")));

// ================= DEFAULT ROUTE (IMPORTANT) =================
// DEFAULT PAGE
app.get("/", (req, res) => {
  res.sendFile(path.join(__dirname, "../frontend/guest_user.html"));
});

// STATIC
app.use(express.static(path.join(__dirname, "../frontend")));

// ================= TEST =================
app.get("/api/test", (req, res) => {
  res.json({ message: "Backend working 🚀" });
});

// ================= TEMP DATABASE =================
let otpStore = {};
let users = {};

// ================= EMAIL SETUP =================
const transporter = nodemailer.createTransport({
  service: "gmail",
  auth: {
    user: "emoheal11@gmail.com",
    pass: "ouqlpmokgqqeuwpy"
  }
});

// ================= SEND OTP =================
app.post("/api/send-otp", async (req, res) => {
  const { email } = req.body;

  if (!email) {
    return res.status(400).json({ message: "Email required ❌" });
  }

  const otp = Math.floor(100000 + Math.random() * 900000);
  otpStore[email] = otp;

  try {
    await transporter.sendMail({
      from: '"EmoHeal 💜" <emoheal11@gmail.com>',
      to: email,
      subject: "EmoHeal Verification Code",
      text: `Your OTP is ${otp}`
    });

    res.json({ message: "OTP sent to email 📩" });

  } catch (error) {
    console.log("❌ Email error:", error);
    res.status(500).json({ message: "Error sending email ❌" });
  }
});

// ================= REGISTER =================
app.post("/api/register", (req, res) => {
  const { email, otp, password, name, username } = req.body;

  if (!email || !otp) {
    return res.status(400).json({ message: "Missing data ❌" });
  }

  if (otpStore[email] != otp) {
    return res.json({ message: "Invalid OTP ❌" });
  }

  users[email] = { email, password, name, username };
  delete otpStore[email];

  res.json({ message: "Registered Successfully ✅" });
});

// ================= LOGIN =================
app.post("/api/login", (req, res) => {
  const { email, password } = req.body;

  const user = users[email];

  if (!user) {
    return res.json({ message: "User not found ❌" });
  }

  if (user.password !== password) {
    return res.json({ message: "Wrong password ❌" });
  }

  res.json({
    message: "Login Successful ✅",
    username: user.username
  });
});

// ================= SERVER =================
app.listen(PORT, () => {
  console.log(`🚀 Server running at http://localhost:${PORT}`);
});