import { useCallback, useEffect, useState } from 'react';
import Button from 'react-bootstrap/Button';
import { AddItemForm } from './AddNewItemForm';
import { ItemDisplay } from './ItemDisplay';
import { StatusMessage } from './StatusMessage';

export function TodoListCard() {
    const [items, setItems] = useState(null);
    const [loadError, setLoadError] = useState(false);
    const [actionError, setActionError] = useState('');

    const loadItems = useCallback(() => {
        setLoadError(false);
        return fetch('/api/items')
            .then((r) => {
                if (!r.ok) throw new Error(`HTTP error ${r.status}`);
                return r.json();
            })
            .then((data) => setItems(Array.isArray(data) ? data : []))
            .catch((err) => {
                console.error('Failed to load items:', err);
                setLoadError(true);
            });
    }, []);

    useEffect(() => {
        loadItems();
    }, [loadItems]);

    const onNewItem = useCallback((newItem) => {
        setItems((prev) => [...(prev ?? []), newItem]);
    }, []);

    const onItemUpdate = useCallback((item) => {
        setItems((prev) =>
            (prev ?? []).map((i) => (i.id === item.id ? item : i)),
        );
    }, []);

    const onItemRemoval = useCallback((item) => {
        setItems((prev) => (prev ?? []).filter((i) => i.id !== item.id));
    }, []);

    // A failed load must never show the empty-state message (FR-012).
    if (loadError) {
        return (
            <>
                <StatusMessage message="Could not load your items." />
                <Button variant="outline-primary" onClick={loadItems}>
                    Try again
                </Button>
            </>
        );
    }

    if (items === null) return 'Loading...';

    return (
        <>
            <AddItemForm onNewItem={onNewItem} />
            <StatusMessage message={actionError} />
            {items.length === 0 && (
                <p className="text-center">No items yet! Add one above!</p>
            )}
            {items.map((item) => (
                <ItemDisplay
                    key={item.id}
                    item={item}
                    onItemUpdate={onItemUpdate}
                    onItemRemoval={onItemRemoval}
                    onReload={loadItems}
                    onActionError={setActionError}
                />
            ))}
        </>
    );
}
