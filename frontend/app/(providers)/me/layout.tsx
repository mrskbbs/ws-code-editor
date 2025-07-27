"use client";
import styles from "./page.module.css";
import { AuthCheck } from "@/components/AuthCheck/AuthCheck";

export default function MeLayout({ children }: { children: React.ReactNode }) {
    return (
        <div className={styles.container}>
            <AuthCheck>{children}</AuthCheck>
        </div>
    );
}
