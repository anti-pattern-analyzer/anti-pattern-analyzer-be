import { Joi } from "celebrate";

export const updateUserSchema = Joi.object({
  name: Joi.string().optional(),
  mobile_no: Joi.string().email().optional()
});
