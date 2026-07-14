import {
	ErrorBoundary,
	hydrate,
	LocationProvider,
	prerender as ssr,
	Route,
	Router,
} from 'preact-iso';
import { Layout } from './components/Layout';
import { Home } from './pages/Home';
import { Login } from './pages/Login';
import { Signup } from './pages/Signup';
import { MyRooms } from './pages/MyRooms';
import { MyProfile } from './pages/MyProfile';
import { RoomCreate } from './pages/RoomCreate';
import { RoomEditor } from './pages/RoomEditor';
import { RoomInvite } from './pages/RoomInvite';
import { DevPreview } from './pages/DevPreview';
import { DevRedirect } from './pages/DevRedirect';
import './style.css';

function DevRoutes() {
	if (!import.meta.env.DEV) return null;

	return (
		<>
			<Route path="/dev" component={DevRedirect} />
			<Route path="/dev/preview" component={DevPreview} />
		</>
	);
}

export function App() {
	return (
		<LocationProvider>
			<ErrorBoundary>
				<Layout>
					<Router>
						<DevRoutes />
						<Route path="/" component={Home} />
						<Route path="/login" component={Login} />
						<Route path="/signup" component={Signup} />
						<Route path="/my/rooms" component={MyRooms} />
						<Route path="/my/profile" component={MyProfile} />
						<Route path="/room/create" component={RoomCreate} />
						<Route path="/room/invite/:inviteToken" component={RoomInvite} />
						<Route path="/room/:roomId" component={RoomEditor} />
					</Router>
				</Layout>
			</ErrorBoundary>
		</LocationProvider>
	);
}

export async function prerender() {
	return await ssr(<App />);
}

if (typeof window !== 'undefined') {
	hydrate(<App />, document.getElementById('app')!);
}