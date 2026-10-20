import React from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import "./base.css";

const root = document.getElementById("root");
if (!root) throw new Error("Missing #root mounting element");
createRoot(root).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
