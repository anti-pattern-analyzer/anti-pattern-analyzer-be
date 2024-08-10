import { traced } from "@sliit-foss/functions";
import context from "express-http-context";
import { retrievedUserByEmail, retrievedUserById, saveUser, updateUserById } from "../repository/user.repository";
import { errors, hashPassword } from "../utils";

export const addUser = async (user) => {
  user.password = await hashPassword(user.password);

  const dbUser = await traced(retrievedUserByEmail)(user.email);
  if (dbUser) {
    throw errors.user_already_exists;
  }

  return traced(saveUser)(user);
};

export const getUser = async (id) => {
  const currentUser = context.get("user");
  if (currentUser._id !== id) {
    throw errors.no_permission;
  }

  const user = await traced(retrievedUserById)(id);
  if (user === null) {
    throw errors.user_not_found;
  }
  return user;
};

export const updateUser = async (id, payload) => {
  const currentUser = context.get("user");
  if (currentUser._id !== id) {
    throw errors.no_permission;
  }

  const user = await traced(retrievedUserById)(id);
  if (user === null) {
    throw errors.user_not_found;
  }
  return traced(updateUserById)(id, payload);
};
