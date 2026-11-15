import { useState } from 'react';
import PropTypes from 'prop-types';
import Button from 'react-bootstrap/Button';
import Form from 'react-bootstrap/Form';
import InputGroup from 'react-bootstrap/InputGroup';
import { StatusMessage } from './StatusMessage';

const MAX_NAME_LENGTH = 255;
const TOO_LONG_MESSAGE = 'Names must be 255 characters or fewer.';
const GENERIC_ERROR =
    'Could not add the item. Your text is still here; try again.';

export function AddItemForm({ onNewItem }) {
    const [newItem, setNewItem] = useState('');
    const [submitting, setSubmitting] = useState(false);
    const [error, setError] = useState('');

    const submitNewItem = (e) => {
        e.preventDefault();
        setSubmitting(true);
        setError('');

        const name = newItem;
        const options = {
            method: 'POST',
            body: JSON.stringify({ name }),
            headers: { 'Content-Type': 'application/json' },
        };
        let tooLong = false;

        fetch('/api/items', options)
            .then((r) => {
                if (!r.ok) {
                    tooLong = r.status === 422 && name.length > MAX_NAME_LENGTH;
                    throw new Error(`HTTP error ${r.status}`);
                }
                return r.json();
            })
            .then((item) => {
                onNewItem(item);
                setNewItem('');
            })
            .catch((err) => {
                console.error('Failed to add item:', err);
                setError(tooLong ? TOO_LONG_MESSAGE : GENERIC_ERROR);
            })
            .finally(() => setSubmitting(false));
    };

    return (
        <Form onSubmit={submitNewItem}>
            <InputGroup className="mb-3">
                <Form.Control
                    value={newItem}
                    onChange={(e) => setNewItem(e.target.value)}
                    type="text"
                    placeholder="New Item"
                    aria-label="New item"
                />
                <Button
                    type="submit"
                    variant="success"
                    disabled={newItem.trim().length === 0}
                    className={submitting ? 'disabled' : ''}
                >
                    {submitting ? 'Adding...' : 'Add Item'}
                </Button>
            </InputGroup>
            <StatusMessage message={error} />
        </Form>
    );
}

AddItemForm.propTypes = {
    onNewItem: PropTypes.func,
};
