import { createRouter, createWebHistory } from 'vue-router'
import DashboardView from '../views/DashboardView.vue'
import SettingsView from '../views/SettingsView.vue'
import TopicDetailView from '../views/TopicDetailView.vue'

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: '/',
            component: () => import('../layouts/DashboardLayout.vue'),
            children: [
                {
                    path: '',
                    name: 'dashboard',
                    component: DashboardView
                },
                {
                    path: 'settings',
                    name: 'settings',
                    component: SettingsView
                },
                {
                    path: 'scripts',
                    name: 'scripts',
                    component: () => import('../views/ScriptsView.vue')
                },
                {
                    path: 'topics',
                    name: 'topics',
                    component: () => import('../views/TopicLibraryView.vue')
                },
                {
                    path: 'topic/:id',
                    name: 'topic-detail',
                    component: TopicDetailView
                }
            ]
        }
    ]
})

export default router
