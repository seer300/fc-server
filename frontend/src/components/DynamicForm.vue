<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  fields: { type: Array, default: () => [] },
  modelValue: { type: Object, default: () => ({}) },
})
const emit = defineEmits(['update:modelValue'])

const form = computed(() => props.modelValue || {})

// 选择器弹层
const picker = ref({ show: false, field: null, columns: [] })
const datePicker = ref({ show: false, field: null, value: [] })

function update(key, value) {
  emit('update:modelValue', { ...form.value, [key]: value })
}

function openPicker(f) {
  const columns = (f.options || []).map((o) => ({
    text: o.label ?? o.value,
    value: o.value ?? o.label,
  }))
  picker.value = { show: true, field: f, columns }
}

function onPickerConfirm({ selectedOptions }) {
  const f = picker.value.field
  const val = selectedOptions[0]?.value
  if (f) update(f.field_key, val)
  picker.value.show = false
}

function openDatePicker(f) {
  const cur = form.value[f.field_key] || '2026-01-01'
  datePicker.value = { show: true, field: f, value: cur.split('-') }
}

function onDateConfirm({ selectedValues }) {
  const f = datePicker.value.field
  const val = selectedValues.join('-')
  if (f) update(f.field_key, val)
  datePicker.value.show = false
}
</script>

<template>
  <div class="dynamic-form">
    <van-cell-group v-for="f in fields" :key="f.id || f.field_key" inset>
      <van-field
        v-if="f.field_type === 'text'"
        :label="f.field_label"
        :required="f.required"
        :model-value="form[f.field_key]"
        @update:model-value="update(f.field_key, $event)"
        :placeholder="'请输入' + f.field_label"
      />
      <van-field
        v-else-if="f.field_type === 'number'"
        :label="f.field_label"
        type="number"
        :required="f.required"
        :model-value="form[f.field_key]"
        @update:model-value="update(f.field_key, $event)"
        :placeholder="'请输入' + f.field_label"
      />
      <van-field
        v-else-if="f.field_type === 'textarea'"
        :label="f.field_label"
        type="textarea"
        autosize
        :required="f.required"
        :model-value="form[f.field_key]"
        @update:model-value="update(f.field_key, $event)"
        :placeholder="'请输入' + f.field_label"
      />
      <van-field
        v-else-if="f.field_type === 'select'"
        :label="f.field_label"
        readonly
        is-link
        :required="f.required"
        :model-value="form[f.field_key]"
        :placeholder="'请选择' + f.field_label"
        @click="openPicker(f)"
      />
      <van-field
        v-else-if="f.field_type === 'date'"
        :label="f.field_label"
        readonly
        is-link
        :required="f.required"
        :model-value="form[f.field_key]"
        placeholder="请选择日期"
        @click="openDatePicker(f)"
      />
    </van-cell-group>

    <van-popup v-model:show="picker.show" position="bottom" round>
      <van-picker
        :columns="picker.columns"
        @confirm="onPickerConfirm"
        @cancel="picker.show = false"
      />
    </van-popup>

    <van-popup v-model:show="datePicker.show" position="bottom" round>
      <van-date-picker
        :model-value="datePicker.value"
        @confirm="onDateConfirm"
        @cancel="datePicker.show = false"
      />
    </van-popup>
  </div>
</template>
