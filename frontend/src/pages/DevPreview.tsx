import { useEffect, useState } from 'preact/hooks';
import { devPages } from '../dev/pages';
import { isDevMockEnabled, setDevMockEnabled } from '../dev/flags';

export function DevPreview() {
	const [mockEnabled, setMockEnabled] = useState(true);

	useEffect(() => {
		setDevMockEnabled(mockEnabled);
	}, [mockEnabled]);

	function previewSrc(path: string): string {
		const url = new URL(path, location.origin);
		url.searchParams.set('__dev_mock', '1');
		return url.pathname + url.search;
	}

	return (
		<section class="dev-preview">
			<h1>Dev Page Preview</h1>
			<p>
				Development only. Visit <code>/dev/preview</code> while running{' '}
				<code>npm run dev</code>.
			</p>

			<label class="dev-preview-toggle">
				<input
					type="checkbox"
					checked={mockEnabled}
					onChange={(e) => setMockEnabled((e.target as HTMLInputElement).checked)}
				/>
				Mock auth &amp; API (preview protected pages without backend)
			</label>

			<ul class="dev-preview-list">
				{devPages.map((page) => (
					<li key={page.path} class="dev-preview-item">
						<div class="dev-preview-meta">
							<h2>
								<a href={previewSrc(page.path)} target="_blank" rel="noopener">
									{page.name}
								</a>
							</h2>
							<p>{page.description}</p>
							<code>{page.path}</code>
							{page.requiresAuth && <span class="dev-preview-badge">auth</span>}
						</div>
						<iframe
							class="dev-preview-frame"
							title={`Preview: ${page.name}`}
							src={mockEnabled || !page.requiresAuth ? previewSrc(page.path) : page.path}
						/>
					</li>
				))}
			</ul>
		</section>
	);
}