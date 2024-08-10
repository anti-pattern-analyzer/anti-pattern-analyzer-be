import express from "express";
import { celebrate, Segments } from "celebrate";
import { traced, tracedAsyncHandler } from "@sliit-foss/functions";
import { response } from "../../utils";
import { login, register } from "../../service/auth.service";
import { loginSchema, registerSchema } from "../../schema/auth.schema";

const auth = express.Router();

auth.post(
  "/login",
  celebrate({ [Segments.BODY]: loginSchema }),
  tracedAsyncHandler(async function loginController(req, res) {
    const data = await traced(login)(req.body);
    return response({ res, message: "Logged in successfully", data });
  })
);

auth.post(
  "/register",
  celebrate({ [Segments.BODY]: registerSchema }),
  tracedAsyncHandler(async function registerController(req, res) {
    const data = await traced(register)(req.body);
    return response({ res, message: "Registered successfully", data });
  })
);

export default auth;
