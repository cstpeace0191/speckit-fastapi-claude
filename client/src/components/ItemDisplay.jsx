import { useState } from 'react';
import PropTypes from 'prop-types';
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Button from 'react-bootstrap/Button';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faPen } from '@fortawesome/free-solid-svg-icons/faPen';
import { faTrash } from '@fortawesome/free-solid-svg-icons/faTrash';
import faCheckSquare from '@fortawesome/fontawesome-free-regular/faCheckSquare';
import faSquare from '@fortawesome/fontawesome-free-regular/faSquare';
import { RenameItemDialog } from './RenameItemDialog';
import './ItemDisplay.scss';

const MISSING_MESSAGE =
    'This item no longer exists. The list has been refreshed.';

// Keeps the HTTP status so callers can tell "item missing" (404) from other failures.
function requestError(response) {
    const error = new Error(`HTTP error ${response.status}`);
    error.status = response.status;
    return error;
}

export function ItemDisplay({
    item,
    onItemUpdate,
    onItemRemoval,
    onReload,
    onActionError,
}) {
    const [editing, setEditing] = useState(false);

    const reportMissing = () => {
        onActionError(MISSING_MESSAGE);
        onReload();
    };

    const toggleCompletion = () => {
        onActionError('');
        fetch(`/api/items/${item.id}`, {
            method: 'PUT',
            // Send only completed, so a stale name cannot overwrite a rename.
            body: JSON.stringify({ completed: !item.completed }),
            headers: { 'Content-Type': 'application/json' },
        })
            .then((r) => {
                if (!r.ok) throw requestError(r);
                return r.json();
            })
            .then(onItemUpdate)
            .catch((err) => {
                console.error('Failed to update item:', err);
                if (err.status === 404) reportMissing();
                else onActionError('Could not update the item. Try again.');
            });
    };

    const removeItem = () => {
        onActionError('');
        fetch(`/api/items/${item.id}`, { method: 'DELETE' })
            .then((r) => {
                if (!r.ok) throw requestError(r);
                onItemRemoval(item);
            })
            .catch((err) => {
                console.error('Failed to remove item:', err);
                if (err.status === 404) reportMissing();
                else onActionError('Could not remove the item. Try again.');
            });
    };

    // Resolves when saved. Rejects with a message the dialog shows.
    const renameItem = (newName) => {
        onActionError('');
        return fetch(`/api/items/${item.id}`, {
            method: 'PUT',
            body: JSON.stringify({ name: newName }),
            headers: { 'Content-Type': 'application/json' },
        })
            .then((r) => {
                if (!r.ok) throw requestError(r);
                return r.json();
            })
            .then((updated) => {
                onItemUpdate(updated);
                setEditing(false);
            })
            .catch((err) => {
                console.error('Failed to rename item:', err);
                if (err.status === 404) {
                    setEditing(false);
                    reportMissing();
                    return;
                }
                throw new Error(
                    err.status === 422
                        ? 'Names must be 255 characters or fewer.'
                        : 'Could not rename the item. Try again.',
                );
            });
    };

    return (
        <Container fluid className={item.completed ? 'item completed' : 'item'}>
            <Row>
                <Col xs={2} className="text-center">
                    <Button
                        className="toggles"
                        size="sm"
                        variant="link"
                        onClick={toggleCompletion}
                        aria-label={
                            item.completed
                                ? `Mark ${item.name} as incomplete`
                                : `Mark ${item.name} as complete`
                        }
                    >
                        <FontAwesomeIcon
                            icon={item.completed ? faCheckSquare : faSquare}
                        />
                        <i
                            className={`far ${
                                item.completed ? 'fa-check-square' : 'fa-square'
                            }`}
                        />
                    </Button>
                </Col>
                <Col xs={6} className="name">
                    {item.name}
                </Col>
                <Col xs={2} className="text-center">
                    <Button
                        size="sm"
                        variant="link"
                        onClick={() => setEditing(true)}
                        aria-label={`Rename ${item.name}`}
                    >
                        <FontAwesomeIcon icon={faPen} />
                    </Button>
                </Col>
                <Col xs={2} className="text-center remove">
                    <Button
                        size="sm"
                        variant="link"
                        onClick={removeItem}
                        aria-label={`Remove ${item.name}`}
                    >
                        <FontAwesomeIcon
                            icon={faTrash}
                            className="text-danger"
                        />
                    </Button>
                </Col>
            </Row>
            {editing && (
                <RenameItemDialog
                    currentName={item.name}
                    onSave={renameItem}
                    onCancel={() => setEditing(false)}
                />
            )}
        </Container>
    );
}

ItemDisplay.propTypes = {
    item: PropTypes.shape({
        id: PropTypes.string,
        name: PropTypes.string,
        completed: PropTypes.bool,
    }),
    onItemUpdate: PropTypes.func,
    onItemRemoval: PropTypes.func,
    onReload: PropTypes.func,
    onActionError: PropTypes.func,
};
