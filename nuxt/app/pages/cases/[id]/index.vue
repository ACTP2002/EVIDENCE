<!-- cases/[id]/index.vue -->

<template>
    <div class="grid grid-cols-12 gap-4">
        <div class="col-span-8 space-y-4">
            <div class="rounded-lg border border-slate-200 bg-white p-4">
                <div class="flex items-start justify-between">
                    <div>
                        <h1 class="text-xl font-semibold">Case {{ id }}</h1>
                        <div class="text-sm text-slate-600 mt-1">Customer profile, transactions, access signals, and
                            linked entities.</div>
                    </div>
                    <div class="flex items-center gap-2">
                        <button class="h-9 px-3 rounded-md border border-slate-200 text-sm hover:bg-slate-50">
                            Generate Case Summary
                        </button>
                        <NuxtLink :to="`/cases/${id}/report`"
                            class="h-9 px-3 rounded-md bg-slate-900 text-white text-sm inline-flex items-center"
                            @click.stop>
                            Generate Report
                        </NuxtLink>

                    </div>
                </div>
            </div>

            <div class="rounded-lg border border-slate-200 bg-white p-4">
                <h2 class="text-sm font-semibold">Timeline</h2>
                <div class="mt-3 space-y-3 text-sm">
                    <div class="flex gap-3">
                        <div class="w-24 text-xs text-slate-500">09:14</div>
                        <div>Login from high-risk jurisdiction via VPN</div>
                    </div>
                    <div class="flex gap-3">
                        <div class="w-24 text-xs text-slate-500">09:22</div>
                        <div>Deposit spike inconsistent with declared income</div>
                    </div>
                    <div class="flex gap-3">
                        <div class="w-24 text-xs text-slate-500">09:35</div>
                        <div>New beneficiary added; transfer initiated</div>
                    </div>
                </div>
            </div>
            <div class="rounded-lg border border-slate-200 bg-white p-4">
                <h2 class="text-sm font-semibold">Remarks</h2>
                <div class="mt-3 space-y-3">
                    <!-- <div class="flex "> -->
                    <textarea id="remarks" rows="4" maxlength="255"
                        class="bg-neutral-secondary-medium border border-default-medium text-heading text-sm rounded-base focus:ring-brand focus:border-brand block w-full px-3 py-2.5 shadow-xs placeholder:text-body"
                        placeholder="Add your remarks..." required></textarea>
                    <div class="flex justify-end">
                        <button class="h-9 px-3 rounded-md bg-slate-900 text-white text-sm">
                            Submit
                        </button>
                    </div>
                    <!-- </div> -->
                </div>
            </div>
        </div>

        <div class="col-span-4 space-y-4">
            <div class="rounded-lg border border-slate-200 bg-white p-4">
                <h2 class="text-sm font-semibold">Why flagged</h2>
                <div class="mt-2 text-xs text-slate-500">Explainable alert with confidence and signal breakdown.</div>

                <div class="mt-4 flex items-center justify-between">
                    <div class="text-sm text-slate-600">Confidence</div>
                    <div class="text-sm font-semibold">89%</div>
                </div>

                <div class="mt-3 space-y-2 text-sm">
                    <div class="flex items-start gap-2">
                        <div
                            class="mt-1 h-5 w-5 rounded-md bg-slate-900 text-white text-xs flex items-center justify-center">
                            1</div>
                        <div>Deposits 1400% above declared income</div>
                    </div>
                    <div class="flex items-start gap-2">
                        <div
                            class="mt-1 h-5 w-5 rounded-md bg-slate-900 text-white text-xs flex items-center justify-center">
                            2</div>
                        <div>73% logins from high-risk jurisdiction via VPN</div>
                    </div>
                    <div class="flex items-start gap-2">
                        <div
                            class="mt-1 h-5 w-5 rounded-md bg-slate-900 text-white text-xs flex items-center justify-center">
                            3</div>
                        <div>Pattern match: similar to 12 confirmed ML cases last quarter</div>
                    </div>
                </div>

                <div class="mt-4 pt-4 border-t border-slate-200">
                    <div class="text-xs font-medium text-slate-600 uppercase tracking-wide">Signal breakdown</div>
                    <div class="mt-2 space-y-2 text-sm">
                        <div class="flex items-center justify-between"><span>Transactions</span><span
                                class="font-medium">0.44</span></div>
                        <div class="flex items-center justify-between"><span>Geo/VPN</span><span
                                class="font-medium">0.31</span></div>
                        <div class="flex items-center justify-between"><span>Network Links</span><span
                                class="font-medium">0.18</span></div>
                        <div class="flex items-center justify-between"><span>Identity</span><span
                                class="font-medium">0.07</span></div>
                    </div>
                </div>
            </div>

            <div class="rounded-lg border border-slate-200 bg-white p-4">
                <h2 class="text-sm font-semibold">Decision</h2>
                <div class="mt-3 grid grid-cols-1 gap-2">
                    <button class="h-9 rounded-md bg-red-600 text-white text-sm">Confirm Fraud</button>
                    <button class="h-9 rounded-md border border-slate-200 text-sm hover:bg-slate-50">False
                        Positive</button>
                    <button class="h-9 rounded-md border border-slate-200 text-sm hover:bg-slate-50">Needs
                        Review</button>
                </div>
                <div class="mt-3 text-xs text-slate-500">
                    Decisions are logged with timestamp, investigator, and rationale for audit review.
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
const route = useRoute();
const id = computed(() => String(route.params.id));
</script>
