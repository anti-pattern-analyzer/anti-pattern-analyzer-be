import express from "express";
import { celebrate, Segments } from "celebrate";
import { traced, tracedAsyncHandler } from "@sliit-foss/functions";
import { response } from "../../utils";
import { getUser, updateUser } from "../../service/user.service";
import { updateUserSchema } from "../../schema/user.schema";

const user = express.Router();

user.get(
  "/:id",
  tracedAsyncHandler(async (req, res) => {
    const user = await traced(getUser)(req.params.id);
    return response({ res, message: "User retrieved successfully", data: user });
  })
);

user.patch(
  "/:id",
  celebrate({ [Segments.BODY]: updateUserSchema }),
  tracedAsyncHandler(async (req, res) => {
    const user = await traced(updateUser)(req.params.id, req.body);
    return response({ res, message: "User updated successfully", data: user });
  })
);

export default user;
