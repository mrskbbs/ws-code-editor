"use client";

import { AuthCheck } from "@/components/AuthCheck/AuthCheck";

export default function MeLayout({ children }: { children: React.ReactNode }) {
    return <AuthCheck>{children}</AuthCheck>;
}
