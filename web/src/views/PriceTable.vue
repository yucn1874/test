<template>
  <div class="price-table-page">
    <el-card class="mb-20">
      <div class="card-header">
        <h2>农产品价格表</h2>
      </div>
      <!-- 筛选部分：分类水平排列 + 搜索框 + 导出按钮 -->
      <div class="filter-section">
        <!-- 分类按钮组 -->
        <div class="category-row">
          <el-button
            v-for="(item, index) in categoryTree"
            :key="index"
            :type="selectedCategory === item.category ? 'primary' : 'default'"
            @click="handleCategorySelect(item.category)"
          >
            {{ item.category }}
          </el-button>
        </div>

        <!-- 搜索 + 导出 -->
        <div class="filter-actions">
          <el-input
            v-model="varietySearch"
            placeholder="请输入品种名称"
            clearable
            class="search-input"
          />
          <el-button type="primary" @click="handleSearchVariety">搜索</el-button>
          <el-button type="info" @click="handleExportCSV">导出CSV</el-button>
        </div>
      </div>
    </el-card>

    <el-card>
      <!-- 新增数据按钮 -->
      <div class="add-section">
        <el-button type="success" icon="el-icon-circle-plus" @click="showAddDialog">
          添加价格数据
        </el-button>
      </div>

      <!-- 数据表格 -->
      <div style="width: 90%; margin: 20px auto 0;">

        <el-table :data="priceList" stripe style="width: 100%; margin-top: 20px;">
          <el-table-column prop="id" label="ID" width="80" align="center" />
          <el-table-column prop="data" label="日期" width="120" align="center" />
          <el-table-column prop="category" label="分类" width="120" align="center" />
          <el-table-column prop="variety" label="品种" width="120" align="center" />
          <el-table-column prop="price" label="价格" width="100" align="center" />
          <el-table-column prop="unit" label="单位" width="120" align="center" />
          <el-table-column prop="area" label="地区" width="120" align="center" />
          <el-table-column prop="province" label="省份" width="120" align="center" />
          <el-table-column label="操作" width="200" align="center">
            <template #default="scope">
              <el-button size="small" type="primary" @click="handleEdit(scope.row)">修改</el-button>
              <el-button size="small" type="danger" @click="handleDelete(scope.row.id)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>


      <div style="display: flex; justify-content: center; margin-top: 20px;">
        <!-- 分页组件 -->
        <el-pagination
          background
          layout="prev, pager, next, jumper"
          :current-page="currentPage"
          :page-size="pageSize"
          :total="totalCount"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- 添加 / 编辑 对话框 -->
    <el-dialog :title="dialogTitle" v-model="showDialog" width="500px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="日期">
          <el-date-picker v-model="form.data" type="date" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item label="分类">
          <el-input v-model="form.category" />
        </el-form-item>
        <el-form-item label="品种">
          <el-input v-model="form.variety" />
        </el-form-item>
        <el-form-item label="价格">
          <el-input-number v-model="form.price" :min="0" :precision="2" />
        </el-form-item>
        <el-form-item label="单位">
          <el-input v-model="form.unit" />
        </el-form-item>
        <el-form-item label="地区">
          <el-input v-model="form.area" />
        </el-form-item>
        <el-form-item label="省份">
          <el-input v-model="form.province" />
        </el-form-item>

      </el-form>
      <template #footer>
        <el-button @click="cancelDialog">取消</el-button>
        <el-button type="primary" @click="confirmDialog">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted } from 'vue';
import { getProductPrices, createProductPrice, updateProductPrice, deleteProductPrice } from '@/api';
import type { ProductPrice } from '@/api/types';

export default defineComponent({
  name: 'PriceTable',
  setup() {
    // 数据
    const priceList = ref<ProductPrice[]>([]);
    const categoryTree = ref([
      { category: '水果' },
      { category: '蔬菜' },
      { category: '水产品' },
      { category: '畜禽产品' },
    ]);

    // 当前选中的分类
    const selectedCategory = ref('');

    // 搜索
    const varietySearch = ref('');

    // 分页
    const currentPage = ref(1);
    const pageSize = ref(10); // 每页显示10条，根据需求可调整
    const totalCount = ref(0);

    // 对话框相关
    const showDialog = ref(false);
    const isEditMode = ref(false);
    const form = ref<ProductPrice>({
      data: '',
      category: '',
      variety: '',
      price: 0,
      area: '',
      unit: '元/公斤',
      province: '',
    });

    const dialogTitle = computed(() => (isEditMode.value ? '编辑价格数据' : '添加价格数据'));

    // 获取数据
    const fetchData = async (page = currentPage.value) => {
      try {
        const params: any = {
          page,
          page_size: pageSize.value,
        };
        if (selectedCategory.value) {
          params.category = selectedCategory.value;
        }
        if (varietySearch.value.trim()) {
          params.variety = varietySearch.value.trim();
        }

        const res = await getProductPrices(params);
        // 假设后端返回 { count, results } 结构
        priceList.value = res.data.results;
        totalCount.value = res.data.count;
      } catch (error) {
        console.error('获取价格数据失败:', error);
      }
    };

    onMounted(() => {
      fetchData();
    });

    // 分类按钮点击
    const handleCategorySelect = (category: string) => {
      selectedCategory.value = category;
      currentPage.value = 1;
      fetchData(1);
    };

    // 搜索品种
    const handleSearchVariety = () => {
      currentPage.value = 1;
      fetchData(1);
    };

    // 分页切换
    const handlePageChange = (page: number) => {
      currentPage.value = page;
      fetchData(page);
    };

    // 新增
    const showAddDialog = () => {
      isEditMode.value = false;
      form.value = {
        data: '',
        category: '',
        variety: '',
        price: 0,
        area: '',
        unit: '元/公斤',
        province: '',
      };
      showDialog.value = true;
    };

    // 编辑
    const handleEdit = (item: ProductPrice) => {
      isEditMode.value = true;
      form.value = { ...item };
      showDialog.value = true;
    };

    // 删除
    const handleDelete = async (id?: number) => {
      if (!id) return;
      if (confirm('确认删除该条价格记录吗？')) {
        try {
          await deleteProductPrice(id);
          fetchData();
        } catch (error) {
          console.error('删除失败:', error);
        }
      }
    };

    // 对话框确认
    const confirmDialog = async () => {
      try {
        if (isEditMode.value && form.value.id) {
          await updateProductPrice(form.value.id, form.value);
        } else {
          await createProductPrice(form.value);
        }
        // 刷新当前页数据
        fetchData();
        showDialog.value = false;
      } catch (error) {
        console.error(isEditMode.value ? '修改失败:' : '添加失败:', error);
      }
    };

    // 对话框取消
    const cancelDialog = () => {
      showDialog.value = false;
    };

    // 导出 CSV
    const handleExportCSV = () => {
      // 定义 BOM
      const BOM = '\uFEFF';
      // 标题行
      let csvContent = 'ID,日期,分类,品种,价格,地区,省份,单位\r\n';
      // 数据行
      priceList.value.forEach((item) => {
        csvContent += `${item.id},${item.data},${item.category},${item.variety},${item.price},${item.area},${item.province},${item.unit}\r\n`;
      });
      // 在内容前加上 BOM
      csvContent = BOM + csvContent;

      // 创建下载链接并触发下载
      const encodedUri = encodeURI('data:text/csv;charset=utf-8,' + csvContent);
      const link = document.createElement('a');
      link.setAttribute('href', encodedUri);
      link.setAttribute('download', 'price_list.csv');
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    };

    return {
      priceList,
      categoryTree,
      selectedCategory,
      varietySearch,
      currentPage,
      pageSize,
      totalCount,
      showDialog,
      dialogTitle,
      form,
      handleCategorySelect,
      handleSearchVariety,
      handlePageChange,
      showAddDialog,
      handleEdit,
      handleDelete,
      confirmDialog,
      cancelDialog,
      handleExportCSV,
    };
  },
});
</script>

<style scoped>
/* 外层容器样式 */
.price-table-page {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

/* 间距 */
.mb-20 {
  margin-bottom: 20px;
}

/* 卡片标题 */
.card-header h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

/* 筛选部分 */
.filter-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 20px;
}

/* 分类按钮组 */
.category-row {
  display: flex;
  gap: 10px;
}

/* 搜索和导出区域 */
.filter-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

/* 搜索框宽度 */
.search-input {
  width: 200px;
}

/* 添加按钮区域 */
.add-section {
  display: flex;
  justify-content: flex-start;
  margin-bottom: 10px;
}

/* 表格操作列 */
.el-table .el-button {
  margin-right: 5px;
}
</style>
