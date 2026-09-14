# 预推免-补编-04-第四题：数据库-SQL查询

[查看原始资料对应章节](<../../../原始资料/26年同济CS预推免复习资料_离线完整版.html#s25>)

> 本篇含“根据回忆补全的题目”、知识点讲解及模拟练习，不能视为完整原题。原解析可能有误，例如127结点满二叉树第7层64结点应为填满。

原文：[https://www.yuque.com/bandaotiehe-gexb9/hsldt8/pzbw7apkgl1q9et6](<https://www.yuque.com/bandaotiehe-gexb9/hsldt8/pzbw7apkgl1q9et6>)

## 第四题：数据库-SQL查询

### 涉及知识点

#### 1. SQL基本查询

**SELECT语句结构**：

```text
SELECT [DISTINCT] 列名列表
FROM 表名列表
[WHERE 条件]
[GROUP BY 分组列 [HAVING 分组条件]]
[ORDER BY 排序列 [ASC|DESC]]
[LIMIT 数量];
```

**执行顺序**：

1. FROM：确定数据源
2. WHERE：过滤行
3. GROUP BY：分组
4. HAVING：过滤分组
5. SELECT：选择列
6. DISTINCT：去重
7. ORDER BY：排序
8. LIMIT：限制结果数量

#### 2. 连接查询

**内连接（INNER JOIN）**：

```text
SELECT * FROM A INNER JOIN B ON A.id = B.a_id;
-- 只返回匹配的行
```

**左外连接（LEFT JOIN）**：

```text
SELECT * FROM A LEFT JOIN B ON A.id = B.a_id;
-- 返回左表所有行，右表没匹配的为NULL
```

**右外连接（RIGHT JOIN）**：

```text
SELECT * FROM A RIGHT JOIN B ON A.id = B.a_id;
-- 返回右表所有行，左表没匹配的为NULL
```

**全外连接（FULL JOIN）**：

```text
SELECT * FROM A FULL JOIN B ON A.id = B.a_id;
-- 返回两表所有行，没匹配的为NULL
```

**交叉连接（CROSS JOIN）**：

```text
SELECT * FROM A CROSS JOIN B;
-- 笛卡尔积，A的每行与B的每行组合
```

#### 3. 子查询

**标量子查询**：返回单个值

```text
SELECT * FROM students 
WHERE age > (SELECT AVG(age) FROM students);
```

**列子查询**：返回一列值，用IN/NOT IN

```text
SELECT * FROM students 
WHERE class_id IN (SELECT id FROM classes WHERE grade = 1);
```

**行子查询**：返回一行

```text
SELECT * FROM students 
WHERE (age, score) = (SELECT MAX(age), MAX(score) FROM students);
```

**表子查询**：返回一个表

```text
SELECT * FROM (
    SELECT name, score FROM students WHERE score >= 60
) AS passed_students;
```

**相关子查询**：内层查询依赖外层

```text
SELECT * FROM students s1
WHERE score > (SELECT AVG(score) FROM students s2 WHERE s2.class_id = s1.class_id);
```

#### 4. 聚合函数

- **COUNT()**：计数（COUNT(\*) 包含NULL，COUNT(列) 不包含）
- **SUM()**：求和
- **AVG()**：平均值
- **MAX()/MIN()**：最大/最小值
- **GROUP\_CONCAT()**：MySQL特有，连接字符串

#### 5. 分组查询

**GROUP BY**：按列分组

```text
SELECT class_id, AVG(score) 
FROM students 
GROUP BY class_id;
```

**HAVING**：过滤分组（聚合条件）

```text
SELECT class_id, AVG(score) AS avg_score
FROM students 
GROUP BY class_id
HAVING avg_score > 80;
```

**WHERE vs HAVING**：

- WHERE：分组前过滤行，不能用聚合函数
- HAVING：分组后过滤组，可以用聚合函数

#### 6. 集合操作

**UNION**：并集，自动去重

```text
SELECT name FROM students
UNION
SELECT name FROM teachers;
```

**UNION ALL**：并集，不去重

```text
SELECT name FROM students
UNION ALL
SELECT name FROM teachers;
```

**INTERSECT**：交集（MySQL不支持，用JOIN实现）
**EXCEPT**：差集（MySQL不支持，用NOT IN实现）

#### 7. 窗口函数（MySQL 8.0+）

**基本语法**：

```text
函数名() OVER (
    [PARTITION BY 分区列]
    [ORDER BY 排序列]
    [ROWS/RANGE 窗口范围]
)
```

**排名函数**：

- **ROW\_NUMBER()**：连续排名（1,2,3,4）
- **RANK()**：并列跳号（1,2,2,4）
- **DENSE\_RANK()**：并列连续（1,2,2,3）

**聚合窗口函数**：

```text
SELECT name, score,
    AVG(score) OVER (PARTITION BY class_id) AS class_avg,
    SUM(score) OVER (ORDER BY score) AS running_total
FROM students;
```

#### 8. 索引与优化

**索引类型**：

- **主键索引**：唯一且非空
- **唯一索引**：值唯一
- **普通索引**：加速查询
- **全文索引**：文本搜索
- **组合索引**：多列索引，遵循最左前缀原则

**索引使用原则**：

- WHERE、JOIN、ORDER BY的列适合建索引
- 区分度高的列适合建索引
- 频繁更新的列不适合建索引
- 小表不需要索引

**查询优化**：

- 避免SELECT \*
- 避免在WHERE中使用函数或计算
- 使用EXPLAIN分析查询计划
- 合理使用索引
- 避免子查询（某些情况下改用JOIN）

### 根据回忆补全的题目

**题目**：给定以下三个表：

**学生表 students**：

| id | name | class\_id | age | score |
| --- | --- | --- | --- | --- |
| 1 | 张三 | 1 | 20 | 85 |
| 2 | 李四 | 1 | 21 | 92 |
| 3 | 王五 | 2 | 20 | 78 |
| 4 | 赵六 | 2 | 22 | 88 |
| 5 | 钱七 | 3 | 21 | 95 |
| 6 | 孙八 | NULL | 20 | 60 |

**班级表 classes**：

| id | name | teacher\_id |
| --- | --- | --- |
| 1 | 软件1班 | 101 |
| 2 | 软件2班 | 102 |
| 3 | 软件3班 | 101 |

**教师表 teachers**：

| id | name | subject |
| --- | --- | --- |
| 101 | 王老师 | 数据库 |
| 102 | 李老师 | 算法 |
| 103 | 张老师 | 网络 |

**问题**：

1. 查询每个班级的平均分，要求显示班级名称和平均分，按平均分降序排列
2. 查询选修了王老师课程的所有学生姓名
3. 查询分数高于本班平均分的学生姓名、班级名称和分数
4. 查询每个班级分数最高的学生信息（使用窗口函数）
5. 查询没有分配班级的学生，以及没有学生的班级（使用FULL JOIN，若数据库不支持则用UNION）

### 详细解析

#### 解答1：查询每个班级的平均分

```text
SELECT 
    c.name AS class_name,
    AVG(s.score) AS avg_score
FROM students s
INNER JOIN classes c ON s.class_id = c.id
GROUP BY c.id, c.name
ORDER BY avg_score DESC;
```

**结果**：

| class\_name | avg\_score |
| --- | --- |
| 软件3班 | 95.00 |
| 软件1班 | 88.50 |
| 软件2班 | 83.00 |

**要点**：

- 使用INNER JOIN排除了class\_id为NULL的学生（孙八）
- GROUP BY需要包含c.id（主键）
- 别名在ORDER BY中可用

#### 解答2：查询选修王老师课程的学生

```text
SELECT DISTINCT s.name
FROM students s
INNER JOIN classes c ON s.class_id = c.id
INNER JOIN teachers t ON c.teacher_id = t.id
WHERE t.name = '王老师';
```

**结果**：

| name |
| --- |
| 张三 |
| 李四 |
| 钱七 |

**要点**：

- 三表连接：students → classes → teachers
- 使用DISTINCT去除可能的重复（虽然此例不会重复）

**另一种写法（子查询）**：

```text
SELECT name
FROM students
WHERE class_id IN (
    SELECT c.id
    FROM classes c
    INNER JOIN teachers t ON c.teacher_id = t.id
    WHERE t.name = '王老师'
);
```

#### 解答3：查询分数高于本班平均分的学生

```text
SELECT 
    s.name,
    c.name AS class_name,
    s.score
FROM students s
INNER JOIN classes c ON s.class_id = c.id
WHERE s.score > (
    SELECT AVG(score)
    FROM students s2
    WHERE s2.class_id = s.class_id
);
```

**结果**：

| name | class\_name | score |
| --- | --- | --- |
| 李四 | 软件1班 | 92 |
| 赵六 | 软件2班 | 88 |

**要点**：

- 相关子查询：内层依赖外层的class\_id
- 对每个学生，子查询计算其班级的平均分
- class\_id为NULL的学生被排除（INNER JOIN）

**另一种写法（窗口函数）**：

```text
SELECT name, class_name, score
FROM (
    SELECT 
        s.name,
        c.name AS class_name,
        s.score,
        AVG(s.score) OVER (PARTITION BY s.class_id) AS class_avg
    FROM students s
    INNER JOIN classes c ON s.class_id = c.id
) AS t
WHERE score > class_avg;
```

#### 解答4：查询每个班级分数最高的学生（窗口函数）

```text
SELECT name, class_name, score
FROM (
    SELECT 
        s.name,
        c.name AS class_name,
        s.score,
        RANK() OVER (PARTITION BY s.class_id ORDER BY s.score DESC) AS rank_in_class
    FROM students s
    INNER JOIN classes c ON s.class_id = c.id
) AS ranked
WHERE rank_in_class = 1;
```

**结果**：

| name | class\_name | score |
| --- | --- | --- |
| 李四 | 软件1班 | 92 |
| 赵六 | 软件2班 | 88 |
| 钱七 | 软件3班 | 95 |

**要点**：

- PARTITION BY class\_id：按班级分区
- ORDER BY score DESC：分数降序
- RANK()：排名（如有并列最高分，都会返回）
- 如只要一个学生，用ROW\_NUMBER()

**不用窗口函数的写法**：

```text
SELECT s.name, c.name AS class_name, s.score
FROM students s
INNER JOIN classes c ON s.class_id = c.id
WHERE s.score = (
    SELECT MAX(score)
    FROM students s2
    WHERE s2.class_id = s.class_id
);
```

#### 解答5：查询未分配班级的学生和无学生的班级

**MySQL不支持FULL JOIN，用UNION实现**：

```text
-- 未分配班级的学生
SELECT s.name AS name, '学生' AS type, '未分配班级' AS status
FROM students s
WHERE s.class_id IS NULL

UNION

-- 没有学生的班级
SELECT c.name AS name, '班级' AS type, '无学生' AS status
FROM classes c
LEFT JOIN students s ON c.id = s.class_id
WHERE s.id IS NULL;
```

**结果**：

| name | type | status |
| --- | --- | --- |
| 孙八 | 学生 | 未分配班级 |

**要点**：

- 第一部分：WHERE class\_id IS NULL找未分配学生
- 第二部分：LEFT JOIN后WHERE s.id IS NULL找无学生班级
- UNION合并结果

**如果数据库支持FULL JOIN**：

```text
SELECT 
    COALESCE(s.name, c.name) AS name,
    CASE 
        WHEN s.class_id IS NULL THEN '学生-未分配班级'
        WHEN s.id IS NULL THEN '班级-无学生'
    END AS status
FROM students s
FULL OUTER JOIN classes c ON s.class_id = c.id
WHERE s.class_id IS NULL OR s.id IS NULL;
```

### 模拟练习题

#### 练习1

给定订单表orders(id, user\_id, amount, order\_date)和用户表users(id, name, city)。

编写SQL查询：

1. 每个城市的总订单金额，按金额降序
2. 查询订单金额超过该用户平均订单金额的订单
3. 查询连续3天都有下单的用户

点击查看答案

**1) 每个城市总订单金额**：SELECT u.city, SUM(o.amount) AS total\_amount FROM orders o INNER JOIN users u ON o.user\_id = u.id GROUP BY u.city ORDER BY total\_amount DESC; **2) 订单金额超过用户平均**：SELECT o.\* FROM orders o WHERE o.amount \> ( SELECT AVG(amount) FROM orders o2 WHERE o2.user\_id = o.user\_id ); **3) 连续3天都有下单的用户**：SELECT DISTINCT o1.user\_id FROM orders o1 INNER JOIN orders o2 ON o1.user\_id = o2.user\_id AND o2.order\_date = DATE\_ADD(o1.order\_date, INTERVAL 1 DAY) INNER JOIN orders o3 ON o1.user\_id = o3.user\_id AND o3.order\_date = DATE\_ADD(o1.order\_date, INTERVAL 2 DAY); 或使用窗口函数（更高效）：SELECT DISTINCT user\_id FROM ( SELECT user\_id, order\_date, LAG(order\_date, 1) OVER (PARTITION BY user\_id ORDER BY order\_date) AS prev1, LAG(order\_date, 2) OVER (PARTITION BY user\_id ORDER BY order\_date) AS prev2 FROM (SELECT DISTINCT user\_id, order\_date FROM orders) AS daily\_orders ) AS t WHERE DATEDIFF(order\_date, prev1) = 1 AND DATEDIFF(prev1, prev2) = 1;

#### 练习2

解释以下查询的区别：

```text
-- 查询A
SELECT * FROM students WHERE class_id IN (SELECT id FROM classes WHERE grade = 1);

-- 查询B
SELECT * FROM students WHERE EXISTS (SELECT 1 FROM classes WHERE id = students.class_id AND grade = 1);

-- 查询C
SELECT s.* FROM students s INNER JOIN classes c ON s.class_id = c.id WHERE c.grade = 1;
```

点击查看答案

**功能上**：三个查询结果相同，都是查询1年级班级的学生。 **执行方式**： **查询A（IN子查询）**：- 先执行子查询，得到1年级班级id列表 - 再在students表中查找class\_id在列表中的记录 - 适合子查询结果集小的情况 **查询B（EXISTS相关子查询）**：- 对students的每一行，执行子查询检查是否存在匹配 - EXISTS只关心是否存在，找到第一个匹配就返回TRUE - 适合外层表小、内层表大的情况 - 如果有索引，性能通常最好 **查询C（JOIN）**：- 直接连接两表，通过ON条件和WHERE过滤 - 最直观的写法 - 如果有合适索引，性能很好 - 如果students.class\_id和classes.id都有索引，通常最快 **性能对比**（一般情况）：- 小表驱动大表：EXISTS \> IN \> JOIN - 大表驱动小表：JOIN \> IN \> EXISTS - 有索引且数据量大：JOIN ≈ EXISTS \> IN - 现代数据库优化器可能将它们优化成相同执行计划 **推荐**：- 默认使用JOIN（最清晰） - 需要检查"存在"语义时用EXISTS - 子查询结果确定很小时用IN

---
