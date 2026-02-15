<!-- <template>
    <div class="min-h-screen bg-slate-50 text-slate-900">
        <div class="flex">
            <aside class="w-64 border-r border-slate-200 bg-white">
                <SidebarNav />
            </aside>

            <main class="flex-1">
                <header class="h-14 flex items-center justify-between px-6 border-b border-slate-200 bg-white">
                    <div class="text-sm text-slate-600">Fraud Investigation Platform</div>
                    <div class="flex items-center gap-3">
                        <div class="text-xs text-slate-500">Workspace: FI Production</div>
                        <div class="h-8 w-8 rounded-full bg-slate-200" aria-hidden="true" />
                    </div>
                </header>

                <div class="p-6">
                    <slot />
                </div>
            </main>
        </div>
    </div>
</template> -->
<template>
    <div class="flex min-h-screen gap-2">
        <!-- Sidebar -->
        <aside
            :class="[
                'bg-white border-r border-gray-200 flex flex-col sticky top-0 h-screen transition-all duration-300',
                sidebarCollapsed ? 'w-[60px]' : 'w-[280px]'
            ]"
        >
            <!-- Sidebar Header - Clickable to toggle collapse -->
            <div
                @click="toggleSidebar"
                class="p-4 border-b border-gray-200 cursor-pointer hover:bg-gray-50 transition-colors"
                :title="sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'"
            >
                <div class="flex items-center gap-3">
                    <svg width="32" height="32" viewBox="0 0 32 32" fill="none" class="flex-shrink-0">
                        <rect width="32" height="32" rx="8" fill="url(#logo-gradient)" />
                        <path d="M16 8L22 12V20L16 24L10 20V12L16 8Z" stroke="white" stroke-width="2"
                            stroke-linejoin="round" />
                        <circle cx="16" cy="16" r="2" fill="white" />
                        <defs>
                            <linearGradient id="logo-gradient" x1="0" y1="0" x2="32" y2="32">
                                <stop stop-color="#00D4FF" />
                                <stop offset="1" stop-color="#0A2540" />
                            </linearGradient>
                        </defs>
                    </svg>
                    <div v-if="!sidebarCollapsed" class="flex-1 min-w-0">
                        <div class="text-base font-bold text-slate-900 tracking-tight">E.V.I.D.E.N.C.E</div>
                        <div class="text-[11px] text-slate-400 uppercase tracking-wider font-medium mt-0.5">
                            Investigation Platform</div>
                    </div>
                </div>
            </div>

            <!-- Navigation -->
            <nav class="flex-1 p-2 overflow-y-auto">
                <NuxtLink to="/" class="nav-item group" exact-active-class="active" :title="sidebarCollapsed ? 'Case Inbox' : ''">
                    <svg width="20" height="20" viewBox="0 0 20 20" fill="none" class="flex-shrink-0">
                        <rect x="2" y="2" width="7" height="7" rx="1.5" stroke="currentColor" stroke-width="1.5" />
                        <rect x="11" y="2" width="7" height="7" rx="1.5" stroke="currentColor" stroke-width="1.5" />
                        <rect x="2" y="11" width="7" height="7" rx="1.5" stroke="currentColor" stroke-width="1.5" />
                        <rect x="11" y="11" width="7" height="7" rx="1.5" stroke="currentColor" stroke-width="1.5" />
                    </svg>
                    <span v-if="!sidebarCollapsed" class="flex-1">Case Inbox</span>
                    <span v-if="!sidebarCollapsed" class="badge">24</span>
                </NuxtLink>

                <NuxtLink to="/analytics" class="nav-item group" :title="sidebarCollapsed ? 'Analytics' : ''">
                    <svg width="20" height="20" viewBox="0 0 20 20" fill="none" class="flex-shrink-0">
                        <path d="M3 14L8 9L11 12L17 6M17 6H13M17 6V10" stroke="currentColor" stroke-width="1.5"
                            stroke-linecap="round" stroke-linejoin="round" />
                    </svg>
                    <span v-if="!sidebarCollapsed" class="flex-1">Analytics</span>
                </NuxtLink>

                <NuxtLink to="/patterns" class="nav-item group" :title="sidebarCollapsed ? 'Pattern Discovery' : ''">
                    <svg width="20" height="20" viewBox="0 0 20 20" fill="none" class="flex-shrink-0">
                        <circle cx="10" cy="5" r="2.5" stroke="currentColor" stroke-width="1.5" />
                        <circle cx="5" cy="15" r="2.5" stroke="currentColor" stroke-width="1.5" />
                        <circle cx="15" cy="15" r="2.5" stroke="currentColor" stroke-width="1.5" />
                        <path d="M8.5 6.5L6.5 13.5M11.5 6.5L13.5 13.5M7.5 15H12.5" stroke="currentColor"
                            stroke-width="1.5" />
                    </svg>
                    <span v-if="!sidebarCollapsed" class="flex-1">Pattern Discovery</span>
                </NuxtLink>

                <div class="h-px bg-gray-200 my-4"></div>

                <NuxtLink to="/reports" class="nav-item group" :title="sidebarCollapsed ? 'Reports' : ''">
                    <svg width="20" height="20" viewBox="0 0 20 20" fill="none" class="flex-shrink-0">
                        <path
                            d="M5 3C4.44772 3 4 3.44772 4 4V16C4 16.5523 4.44772 17 5 17H15C15.5523 17 16 16.5523 16 16V7L12 3H5Z"
                            stroke="currentColor" stroke-width="1.5" />
                        <path d="M12 3V7H16" stroke="currentColor" stroke-width="1.5" />
                    </svg>
                    <span v-if="!sidebarCollapsed" class="flex-1">Reports</span>
                </NuxtLink>

                <NuxtLink to="/settings" class="nav-item group" :title="sidebarCollapsed ? 'Settings' : ''">
                    <svg width="20" height="20" viewBox="0 0 20 20" fill="none" class="flex-shrink-0">
                        <circle cx="10" cy="10" r="2.5" stroke="currentColor" stroke-width="1.5" />
                        <path
                            d="M10 2V4M10 16V18M18 10H16M4 10H2M15.6 4.4L14.2 5.8M5.8 14.2L4.4 15.6M15.6 15.6L14.2 14.2M5.8 5.8L4.4 4.4"
                            stroke="currentColor" stroke-width="1.5" stroke-linecap="round" />
                    </svg>
                    <span v-if="!sidebarCollapsed" class="flex-1">Settings</span>
                </NuxtLink>
            </nav>

            <!-- Sidebar Footer -->
            <div class="p-2 border-t border-gray-200">
                <div
                    :class="[
                        'flex items-center gap-3 p-2 rounded-lg hover:bg-gray-50 transition-colors cursor-pointer',
                        sidebarCollapsed ? 'justify-center' : ''
                    ]"
                >
                    <div
                        class="w-9 h-9 rounded-full bg-gradient-to-br from-accent to-primary flex items-center justify-center text-white text-sm font-bold flex-shrink-0">
                        SJ
                    </div>
                    <div v-if="!sidebarCollapsed" class="flex-1 min-w-0">
                        <div class="text-sm font-semibold text-slate-900 truncate">Sarah Johnson</div>
                        <div class="text-xs text-slate-400 truncate">Senior Investigator</div>
                    </div>
                </div>
            </div>
        </aside>

        <!-- Main Content -->
        <main class="flex-1 overflow-x-hidden bg-slate-50">
            <slot />
        </main>
    </div>
</template>

<script setup>
const sidebarCollapsed = useState('sidebarCollapsed', () => false)

const toggleSidebar = () => {
    sidebarCollapsed.value = !sidebarCollapsed.value
}
</script>

<style scoped>
.nav-item {
    @apply flex items-center gap-3 px-3 py-2.5 rounded-lg text-slate-500 text-sm font-medium transition-all mb-1 relative;
}

.nav-item:hover {
    @apply bg-gray-50 text-slate-900;
}

.nav-item.active {
    @apply bg-primary text-white;
}

.nav-item.active::before {
    content: '';
    @apply absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-5 bg-accent rounded-r-sm;
}

.badge {
    @apply bg-risk-critical text-white text-[11px] font-semibold px-2 py-0.5 rounded-full font-mono;
}

.nav-item.active .badge {
    @apply bg-accent text-primary;
}
</style>
