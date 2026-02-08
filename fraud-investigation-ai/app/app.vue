<!-- <template>
  <NuxtRouteAnnouncer />
  <NuxtPage />
</template> -->

<template>
  <div id="app" class="container mx-auto mt-4">
    <NuxtLayout>
      <NuxtPage />
    </NuxtLayout>
  </div>
</template>

<script setup>
useHead({
  title: 'Fraud Investigation Platform',
  meta: [
    { name: 'description', content: 'AI-Powered Fraud Detection & Investigation' }
  ]
})
</script>

<style>
/* #app {
  min-height: 100vh;
} */
</style>
