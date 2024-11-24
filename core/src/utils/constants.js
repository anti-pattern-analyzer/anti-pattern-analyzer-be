import createError from "http-errors";

export const errors = {
  missing_token: createError(401, "Bearer token is missing"),
  invalid_token: createError(401, "Token is invalid"),
  cancelled_token: createError(401, "Token has been revoked"),
  invalid_password: createError(401, "Invalid password"),
  invalid_email: createError(401, "Invalid email"),
  invalid_mobile_no: createError(401, "Invalid mobile number"),
  token_expired: createError(401, "Token has expired"),
  no_permission: createError(403, "You don't have permission"),
  user_already_exists: createError(409, "User already exists"),
  user_not_found: createError(404, "User not found"),
  post_not_found: createError(404, "Post not found"),
  already_liked: createError(409, "Post already liked"),
};
