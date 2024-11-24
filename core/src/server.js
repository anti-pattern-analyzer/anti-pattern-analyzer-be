import express from "express";
import expressHealth from "express-health-middleware";
import context from "express-http-context";
import cors from "cors";
import helmet from "helmet";
import routes from "./routes";
import config from "./config";
import { authorizer, errorHandler, resourceNotFoundHandler } from "./middleware";
import { connectMongo } from "./database";

const initialize = () => {
  const app = express();

  app.use(express.json());

  app.use(express.urlencoded({ extended: true }));

  app.use(cors({
    origin: '*'
  }));
  app.use(helmet());

  app.use("/system", expressHealth());

  app.use(context.middleware);

  connectMongo();

  app.use("/api", authorizer, routes);

  app.use(resourceNotFoundHandler);

  app.use(errorHandler);

  global.__basedir = __dirname;

  app.listen(config.PORT, () => {
    console.log(`Server is listening on port ${config.PORT}`);
  });
};

initialize();
