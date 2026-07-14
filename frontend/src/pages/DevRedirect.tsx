import { useEffect } from 'preact/hooks';
import { useLocation } from 'preact-iso';

export function DevRedirect() {
	const { route } = useLocation();

	useEffect(() => {
		route('/dev/preview');
	}, [route]);

	return <p>Redirecting to dev preview...</p>;
}