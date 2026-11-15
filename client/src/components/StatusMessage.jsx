import PropTypes from 'prop-types';

// Always rendered, so screen readers announce a message when it appears.
export function StatusMessage({ message, variant = 'danger' }) {
    return (
        <div role="status" aria-live="polite" className="mt-2">
            {message && (
                <div className={`alert alert-${variant} py-2 mb-0`}>
                    {message}
                </div>
            )}
        </div>
    );
}

StatusMessage.propTypes = {
    message: PropTypes.string,
    variant: PropTypes.string,
};
