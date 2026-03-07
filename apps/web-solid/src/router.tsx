import { createRouter, createRootRoute, createRoute, Outlet } from '@tanstack/solid-router'
import { LoginPage } from './pages/LoginPage'
import { DashboardPage } from './pages/DashboardPage'
import { PRReviewPage } from './pages/PRReviewPage'
import { loadSession } from './stores/session'
import { onMount } from 'solid-js'

function Root() {
  onMount(() => loadSession())
  return <Outlet />
}

const rootRoute = createRootRoute({ component: Root })
const loginRoute = createRoute({ getParentRoute: () => rootRoute, path: '/login', component: LoginPage })
const dashboardRoute = createRoute({ getParentRoute: () => rootRoute, path: '/dashboard', component: DashboardPage })
const prRoute = createRoute({ getParentRoute: () => rootRoute, path: '/pr/$owner/$repo/$number', component: PRReviewPage })

const routeTree = rootRoute.addChildren([loginRoute, dashboardRoute, prRoute])
export const router = createRouter({ routeTree })

declare module '@tanstack/solid-router' {
  interface Register { router: typeof router }
}
