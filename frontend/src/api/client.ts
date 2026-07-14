import xior from 'xior';

export const api = xior.create({
	baseURL: '/api/v1',
	withCredentials: true,
});