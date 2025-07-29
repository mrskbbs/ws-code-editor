import React, { useCallback, useState } from "react";

export function useModal(init_value: boolean) {
    const [content, setContent] = useState(() => null as React.ReactNode);
    const [is_open, setIsOpen] = useState(() => init_value);

    const open = useCallback((content: React.ReactNode) => {
        setIsOpen(() => true);
        setContent(() => content);
    }, []);
    const close = useCallback(() => {
        setIsOpen(() => false);
        setContent(() => null);
    }, []);

    return { is_open, open, close, content };
}
