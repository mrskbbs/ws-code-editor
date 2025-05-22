"use client";
import { useEffect } from "react";
import "./globals.css";

export default function RootLayout({
    children,
}: Readonly<{
    children: React.ReactNode;
}>) {
    useEffect(() => {
        (async () => await fetch(`http://localhost:5000/auth/token`, { method: "GET", credentials: "include" }))();
    }, []);
    return (
        <html lang="en">
            <body>
                {children}
                <footer>
                    <p>mrskbbs&copy; {new Date().getFullYear()} </p>
                    <a href="https://t.me/mrskbbs">Telegram</a>
                    <a href="https://github.com/mrskbbs">Github</a>
                </footer>
            </body>
        </html>
    );
}
