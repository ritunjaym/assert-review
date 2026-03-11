import { createRouter, createRootRoute, createRoute, redirect, Outlet } from '@tanstack/solid-router'
import { loadSession } from './stores/session'
import { lazy, Suspense, onMount } from 'solid-js'

// Lazy-load route components for code-splitting — each page is a separate chunk
const LoginPage = lazy(() => import('./pages/LoginPage').then(m => ({ default: m.LoginPage })))
const DashboardPage = lazy(() => import('./pages/DashboardPage').then(m => ({ default: m.DashboardPage })))
const PRReviewPage = lazy(() => import('./pages/PRReviewPage').then(m => ({ default: m.PRReviewPage })))

function Root() {
  onMount(() => loadSession())
  return (
    <Suspense fallback={<div style={{ display: 'none' }} />}>
      <Outlet />
    </Suspense>
  )
}

const rootRoute = createRootRoute({ component: Root })
const indexRoute = createRoute({ getParentRoute: () => rootRoute, path: '/', beforeLoad: () => { throw redirect({ to: '/login' }) } })
const loginRoute = createRoute({ getParentRoute: () => rootRoute, path: '/login', component: LoginPage })
const dashboardRoute = createRoute({ getParentRoute: () => rootRoute, path: '/dashboard', component: DashboardPage })
const prRoute = createRoute({ getParentRoute: () => rootRoute, path: '/pr/$owner/$repo/$number', component: PRReviewPage })

const routeTree = rootRoute.addChildren([indexRoute, loginRoute, dashboardRoute, prRoute])
export const router = createRouter({ routeTree })

declare module '@tanstack/solid-router' {
  interface Register { router: typeof router }
}
