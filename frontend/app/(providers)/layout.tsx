"use client";

import { auth_store } from "@/stores/auth";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React, { useEffect, useState } from "react";

export default function ProvidersLayout({ children }: { children: React.ReactNode }) {
    const [queryClient] = useState(() => new QueryClient());
    useEffect(() => {
        auth_store.update();
    }, []);
    return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
}
