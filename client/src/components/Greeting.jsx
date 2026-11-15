import { useEffect, useState } from 'react';

export function Greeting() {
    const [greeting, setGreeting] = useState(null);

    useEffect(() => {
        fetch('/api/greeting')
            .then((res) => {
                if (!res.ok) throw new Error(`HTTP error ${res.status}`);
                return res.json();
            })
            .then((data) => setGreeting(data?.greeting || ''))
            .catch((err) => console.error('Failed to load greeting:', err));
    }, [setGreeting]);

    if (!greeting) return null;

    return <h1 className="text-center mb-5">{greeting}</h1>;
}
