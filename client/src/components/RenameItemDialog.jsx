import { useState } from 'react';
import PropTypes from 'prop-types';
import Button from 'react-bootstrap/Button';
import Form from 'react-bootstrap/Form';
import Modal from 'react-bootstrap/Modal';
import { StatusMessage } from './StatusMessage';

const MAX_NAME_LENGTH = 255;
const TOO_LONG_MESSAGE = 'Names must be 255 characters or fewer.';

// Mounted only while open, so each opening starts from the item's current name.
// react-bootstrap returns focus to the trigger button when the dialog closes.
export function RenameItemDialog({ currentName, onSave, onCancel }) {
    const [name, setName] = useState(currentName);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState('');

    const trimmed = name.trim();
    const tooLong = trimmed.length > MAX_NAME_LENGTH;
    const canSave = trimmed.length > 0 && !tooLong && !saving;

    const save = (e) => {
        e.preventDefault();
        if (!canSave) return;
        setSaving(true);
        setError('');
        onSave(trimmed).catch((err) => {
            setError(err.message);
            setSaving(false);
        });
    };

    return (
        <Modal show onHide={onCancel} centered>
            <Form onSubmit={save}>
                <Modal.Header closeButton>
                    <Modal.Title as="h2" className="h5">
                        Rename item
                    </Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    <Form.Group controlId="rename-item-input">
                        <Form.Label>Name</Form.Label>
                        <Form.Control
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                            type="text"
                            autoFocus
                        />
                    </Form.Group>
                    <StatusMessage
                        message={tooLong ? TOO_LONG_MESSAGE : error}
                    />
                </Modal.Body>
                <Modal.Footer>
                    <Button variant="secondary" onClick={onCancel}>
                        Cancel
                    </Button>
                    <Button type="submit" variant="primary" disabled={!canSave}>
                        {saving ? 'Saving...' : 'Save'}
                    </Button>
                </Modal.Footer>
            </Form>
        </Modal>
    );
}

RenameItemDialog.propTypes = {
    currentName: PropTypes.string,
    onSave: PropTypes.func,
    onCancel: PropTypes.func,
};
