<template>
    <div class="p-4">
        <div class="mb-4">
            <div class="text-xs tracking-wide text-slate-500 uppercase">Navigation</div>
            <div class="mt-2 text-lg font-semibold">Investigations</div>
        </div>

        <nav class="space-y-1">
            <NuxtLink to="/cases"
                class="flex items-center gap-2 px-3 py-2 rounded-md text-sm hover:bg-slate-50 border border-transparent"
                active-class="bg-slate-50 border-slate-200">
                <span class="h-2 w-2 rounded-full bg-slate-400" aria-hidden="true"></span>
                Case Inbox
            </NuxtLink>

            <NuxtLink to="/reports"
                class="flex items-center gap-2 px-3 py-2 rounded-md text-sm hover:bg-slate-50 border border-transparent"
                active-class="bg-slate-50 border-slate-200">
                <span class="h-2 w-2 rounded-full bg-slate-400" aria-hidden="true"></span>
                Reports
            </NuxtLink>
        </nav>

        <div class="mt-6 pt-6 border-t border-slate-200">
            <div class="text-xs text-slate-500 uppercase tracking-wide">Queue Health</div>
            <div class="mt-2 grid grid-cols-2 gap-2 text-xs">
                <div class="rounded-md border border-slate-200 bg-slate-50 p-2">
                    <div class="text-slate-500">Open</div>
                    <div class="text-base font-semibold">128</div>
                </div>
                <div class="rounded-md border border-slate-200 bg-slate-50 p-2">
                    <div class="text-slate-500">High Risk</div>
                    <div class="text-base font-semibold">37</div>
                </div>
            </div>
        </div>
    </div>
</template>
