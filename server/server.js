/// ================= IMPORTS =================
const express = require("express");
const path = require("path");
const nodemailer = require("nodemailer");
const cors = require("cors");

// ================= APP =================
const app = express();
const PORT = 5000;

// ================= MIDDLEWARE =================
app.use(express.json());
app.use(cors());

// ================= STATIC FILES =================
app.use(express.static(path.join(__dirname, "../client")));

// ================= TEMP DATABASE =================
let otpStore = {};
let users = {};

// ================= 🔥 GMAIL CONFIG =================
const transporter = nodemailer.createTransport({
  service: "gmail",
  auth: {
    user: "emoheal11@gmail.com",        // 👈 new gmail daal
    pass: "yjnammbalyuliszi"      // 👈 app password (without spaces)
  },
  tls: {
    rejectUnauthorized: false
  }
});

// ================= TEST CONNECTION =================
transporter.verify((err, success) => {
  if (err) {
    console.log("❌ MAIL ERROR:", err);
  } else {
    console.log("✅ Gmail ready to send mails");
  }
});

// ================= SEND OTP =================
app.post("/api/send-otp", async (req, res) => {
  console.log("👉 OTP route hit");

  const { email } = req.body;

  if (!email) {
    return res.status(400).json({ message: "Email required ❌" });
  }

  const otp = Math.floor(100000 + Math.random() * 900000).toString();
  otpStore[email] = otp;

  console.log("Generated OTP:", otp);

  try {
    await transporter.sendMail({
      from: "emoheal11@gmail.com",
      to: email,
      subject: "EmoHeal Verification Code",
      text: `Your OTP is ${otp}`
    });

    console.log("✅ Email sent");

    res.json({ message: "OTP sent to email 📩" });

  } catch (error) {
    console.log("❌ FULL ERROR:", error);
    res.status(500).json({ message: "Error sending email ❌" });
  }
});

// ================= REGISTER =================
app.post("/api/register", (req, res) => {
  console.log("👉 Register route hit");

  const { email, otp, password, name, username } = req.body;

  if (!email || !otp) {
    return res.status(400).json({ message: "Missing data ❌" });
  }

  if (otpStore[email] !== otp) {
    console.log("❌ Wrong OTP");
    return res.json({ message: "Invalid OTP ❌" });
  }

  users[email] = { email, password, name, username };

  delete otpStore[email];

  console.log("✅ User saved:", users[email]);

  res.json({ message: "Registered Successfully ✅" });
});

// ================= LOGIN =================
app.post("/api/login", (req, res) => {
  console.log("👉 Login route hit");

  const { email, password } = req.body;

  const user = users[email];

  if (!user) {
    return res.json({ message: "User not found ❌" });
  }

  if (user.password !== password) {
    return res.json({ message: "Wrong password ❌" });
  }

  res.json({ message: "Login Successful ✅" });
});

// ================= START SERVER =================
app.listen(PORT, () => {
  console.log(`🚀 Server running at http://localhost:${PORT}`);
});
