import "./globals.css";

export default function RootLayout({
    children,
}: Readonly<{
    children: React.ReactNode;
}>) {
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
