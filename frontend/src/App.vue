<template>
  <div id="app">
    <el-menu mode="horizontal" router active-text-color="#409EFF">
      <el-menu-item index="/">问答咨询</el-menu-item>
      <el-menu-item index="/image">图像识别</el-menu-item>
      <el-menu-item index="/inspection">检查记录</el-menu-item>
    </el-menu>
    <div style="padding: 20px; max-width: 1200px; margin: 0 auto;">
      <router-view />
    </div>
  </div>
</template>

<script setup>
</script>

<style>
body { margin: 0; font-family: 'Segoe UI', sans-serif; background: #f5f7fa; }
</style>