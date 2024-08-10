import bcrypt from "bcryptjs";
import { traced } from "@sliit-foss/functions";
import createError from "http-errors";
import { retrievedUserByEmail } from "../repository/user.repository";
import { errors, generateTokens } from "../utils";
import { addUser } from "./user.service";

export const login = async (payload) => {
  const user = await traced(retrievedUserByEmail)(payload.email);
  if (!user) {
    throw createError(401, errors.invalid_email);
  }
  const isPasswordValid = await bcrypt.compare(payload.password, user.password);
  if (!isPasswordValid) {
    throw createError(401, errors.invalid_password);
  }
  const tokens = generateTokens(user);
  return { user, ...tokens };
};

export const register = async (payload) => {
  const user = await traced(retrievedUserByEmail)(payload.email);
  if (user) {
    throw createError(401, "User already exists");
  }
  return addUser(payload);
};
