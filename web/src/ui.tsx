import React from "react";
import * as DialogPrimitive from "@radix-ui/react-dialog";

type ButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "default" | "ghost" | "secondary" | "outline" | "link";
  size?: "sm" | "icon-sm" | "default";
};

export function Button({ variant = "default", size = "default", className = "", type = "button", ...props }: ButtonProps) {
  return <button type={type} className={["uiButton", "uiButton--" + variant, "uiButton--" + size, className].filter(Boolean).join(" ")} {...props} />;
}

export function Input(props: React.InputHTMLAttributes<HTMLInputElement>) {
  return <input {...props} className={["uiInput", props.className].filter(Boolean).join(" ")} />;
}

export const Dialog = DialogPrimitive.Root;
export const DialogTitle = DialogPrimitive.Title;
export const DialogDescription = DialogPrimitive.Description;

export function DialogContent({ children, className = "" }: React.PropsWithChildren<{ className?: string }>) {
  return (
    <DialogPrimitive.Portal>
      <DialogPrimitive.Overlay className="uiDialogOverlay" />
      <DialogPrimitive.Content className={["uiDialogContent", className].join(" ")}>
        <DialogPrimitive.Close className="uiDialogClose" aria-label="Close details">×</DialogPrimitive.Close>
        {children}
      </DialogPrimitive.Content>
    </DialogPrimitive.Portal>
  );
}
