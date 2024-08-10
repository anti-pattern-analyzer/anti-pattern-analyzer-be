import User from "../model/user.model";

export const saveUser = (user) => {
  return User.create(user);
};

export const retrievedUserById = (id) => {
  return User.findById(id).lean();
};

export const retrievedUserByEmail = (email) => {
  return User.findOne({ email }).lean();
};

export const retrieveUsers = (filters = {}, sorts = {}, page, limit) => {
  if (page && limit) {
    return User.paginate(filters, { sort: sorts, page, limit, lean: true });
  }
  return User.find(filters).sort(sorts).lean();
};

export const updateUserById = (id, user) => {
  return User.findByIdAndUpdate(id, user, { new: true }).lean();
};

export const deleteUserById = (id) => {
  return User.findByIdAndUpdate(id, { is_active: false }, { new: true }).lean();
};

export const getAdmin = () => {
  return User.findOne({ role: "ADMIN" });
};
